MODALS = r"""<div class="modal-overlay" id="createModal">
          <div class="modal">
            <div class="modal-title">Create Bot</div>
            <div class="modal-text">Enter a name for the new bot.</div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1;">
                <input id="createBotName" placeholder="e.g. cally-eth" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideCreateModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmCreateBot()">Create</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="modeConfirmModal">
          <div class="modal">
            <div class="modal-title">Confirm Trading Mode Change</div>
            <div class="modal-text" id="modeConfirmText">Switch trading mode?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideModeConfirmModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmTradingModeChange()">Confirm</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="saveModal">
          <div class="modal">
            <div class="modal-title">Save Changes</div>
            <div class="modal-text">Save config and all bot files for this bot?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideSaveModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmSaveAll()">Save</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="createStrategyModal">
          <div class="modal">
            <div class="modal-title">Create Strategy</div>
            <div class="modal-text">Enter a strategy name.</div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1;">
                <input id="createStrategyName" placeholder="e.g. mean-reversion" />
              </div>
            </div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1; max-width:140px;">
                <input id="createStrategyEmoji" list="strategyEmojiList" placeholder="🧠" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideCreateStrategyModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmCreateStrategy()">Create</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="deleteStrategyModal">
          <div class="modal">
            <div class="modal-title">Delete Strategy</div>
            <div class="modal-text" id="deleteStrategyText">Are you sure you want to delete this strategy?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideDeleteStrategyModal()">Cancel</button>
              <button class="btn-danger" onclick="confirmDeleteStrategy()">Delete</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="deleteModal">
          <div class="modal">
            <div class="modal-title">Delete Bot</div>
            <div class="modal-text" id="deleteModalText">Are you sure you want to delete this bot?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideDeleteModal()">Cancel</button>
              <button class="btn-danger" onclick="confirmDeleteBot()">Delete</button>
            </div>
          </div>
        </div>

        <datalist id="botEmojiList">
          <option value="🤖"></option>
          <option value="📈"></option>
          <option value="📉"></option>
          <option value="⚡"></option>
          <option value="🎯"></option>
          <option value="🛡️"></option>
          <option value="🔥"></option>
          <option value="🧠"></option>
        </datalist>

        <datalist id="strategyEmojiList">
          <option value="🧠"></option>
          <option value="📈"></option>
          <option value="📉"></option>
          <option value="⚡"></option>
          <option value="🎯"></option>
          <option value="🛡️"></option>
          <option value="🔁"></option>
          <option value="🌊"></option>
          <option value="🔥"></option>
          <option value="🤖"></option>
        </datalist>

        """
